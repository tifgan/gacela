import torch
from torch import nn

from model.borderEncoder import BorderEncoder
from model.discriminatorpow2loss import Discriminator
from model.generator import Generator

import time
from utils.colorize import colorize

__author__ = 'Andres'


def train(args, device, train_loader, epoch, summary_writer):
    discriminators = nn.ModuleList(
            [Discriminator(args['discriminator'], args['discriminator_in_shape']) for _ in range(3)]
        ).to(device)

    left_border_encoder = BorderEncoder(args['borderEncoder']).to(device)
    right_border_encoder = BorderEncoder(args['borderEncoder']).to(device)

    generator = Generator(args['generator'], args['generator_input']).to(device)

    optim_g = torch.optim.Adam(list(generator.parameters()) + list(left_border_encoder.parameters()) +
                               list(right_border_encoder.parameters()),
                               lr=args['optimizer']['generator']['learning_rate'],
                               betas=(args['optimizer']['generator']['kwargs']))
    optim_d = torch.optim.Adam(discriminators.parameters(),
                               lr=args['optimizer']['discriminator']['learning_rate'],
                               betas=(args['optimizer']['discriminator']['kwargs']))

    # try:
    left_border_encoder.train()
    right_border_encoder.train()
    generator.train()
    discriminators.train()
    print('try')
    start_time = time.time()
    prev_iter_time = start_time
    # train_loader = tqdm.tqdm(train_loader)
    for batch_idx, data in enumerate(train_loader):

        data = data.to(device).float()
        data = data.view(args['optimizer']['batch_size'], *args['spectrogram_shape'])

        optim_g.zero_grad()
        optim_d.zero_grad()

        real_spectrograms = data[::2]

        fake_left_borders = data[1::2, :, :, :args['split'][0]]
        fake_right_borders = data[1::2, :, :, args['split'][0]+args['split'][1]:]

        encoded_left_border = left_border_encoder(fake_left_borders)
        encoded_right_border = right_border_encoder(fake_right_borders)
        generated_spectrograms = generator(torch.cat((encoded_left_border, encoded_right_border), 1))

        fake_spectrograms = torch.cat((fake_left_borders, generated_spectrograms, fake_right_borders), 3)
        gen_loss = 0
        disc_loss = 0

        for index, discriminator in enumerate(discriminators):
            scale = 2 ** index
            time_axis = args['spectrogram_shape'][2]
            start = int((time_axis - (time_axis // 4) * scale) / 2)
            end = time_axis - start
            x_fake = fake_spectrograms[:, :, :, start:end:scale]
            x_real = real_spectrograms[:, :, :, start:end:scale]

            d_loss_f = discriminator(x_fake)
            d_loss_r = discriminator(x_real)

            gen_loss += torch.mean(torch.pow(d_loss_f - 1.0, 2))

            disc_loss += torch.mean(torch.pow(d_loss_r - 1.0, 2)) + torch.mean(torch.pow(d_loss_f, 2))

            # d_loss_gp += calc_gradient_penalty(discriminator, x_real, x_fake, args['gamma_gp'])
        # disc_loss = -(d_loss_r - d_loss_f) + d_loss_gp

        gen_loss.backward(retain_graph=True)
        optim_g.step()

        for _ in range(args['optimizer']['n_critic'] - 1):
            optim_d.zero_grad()
            disc_loss.backward(retain_graph=True)
            optim_d.step()

        optim_d.zero_grad()
        disc_loss.backward()
        optim_d.step()

        if batch_idx % args['log_interval'] == 0:
            current_time = time.time()

            print(" * Epoch: [{:2d}] [{:4d}/{:4d} ({:.0f}%)] "
                  "Counter:{:2d}\t"
                  "({:4.1f} min\t"
                  "{:4.3f} examples/sec\t"
                  "{:4.2f} sec/batch)\n"
                  "   Disc batch loss:{:.8f}\t"
                  "   Gen batch loss:{:.8f}\t".format(
                int(epoch),
                int(batch_idx*len(data)),
                int(len(train_loader.dataset)/len(data)), 100. * batch_idx / len(train_loader), int(batch_idx),
                (current_time - start_time) / 60,
                args['log_interval'] * args['optimizer']['batch_size'] / (current_time - prev_iter_time),
                (current_time - prev_iter_time) / args['log_interval'],
                disc_loss.item(),
                gen_loss.item()))
            prev_iter_time = current_time
        if batch_idx % args['tensorboard_interval'] == 0:
            summary_writer.add_scalar("Disc/Neg_Loss", -disc_loss, global_step=batch_idx)
            summary_writer.add_scalar("Disc/Neg_Critic", d_loss_f.mean() - d_loss_r.mean(), global_step=batch_idx)
            summary_writer.add_scalar("Disc/Loss_f", d_loss_f.mean(), global_step=batch_idx)
            summary_writer.add_scalar("Disc/Loss_r", d_loss_r.mean(), global_step=batch_idx)
            summary_writer.add_scalar("Gen/Loss", gen_loss, global_step=batch_idx)

            for index in range(4):
                summary_writer.add_image("images/Real_Image/" + str(index), colorize(real_spectrograms[index]), global_step=batch_idx)
                summary_writer.add_image("images/Fake_Image/" + str(index), colorize(fake_spectrograms[index], -1, 1), global_step=batch_idx)
            # except Exception as e:
        # print(e)

