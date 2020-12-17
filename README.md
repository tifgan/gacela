# [GACELA - Generative adversarial context encoder for audio inpainting](https://ieeexplore.ieee.org/document/9257074)


We introduce GACELA, a conditional generative adversarial network (cGAN) designed to restore missing audio data with durations ranging between hundreds of milliseconds and a few seconds, i.e., to perform long-gap audio inpainting. While previous work either addressed shorter gaps or relied on exemplars by copying available information from other signal parts, GACELA addresses the inpainting of long gaps in two aspects. First, it considers various time scales of audio information by relying on five parallel discriminators with increasing resolution of receptive fields. Second, it is conditioned not only on the available information surrounding the gap, i.e., the context, but also on the latent variable of the cGAN. This addresses the inherent multi-modality of audio inpainting for such long gaps while providing the user with different inpainting options. GACELA was evaluated in listening tests on music signals of varying complexity and varying gap durations from 375ms to 1500ms. Under laboratory conditions, our subjects were often able to detect the inpainting. However, the severity of the inpainted artifacts was rated between not disturbing and mildly disturbing. GACELA represents a framework capable of integrating future improvements such as processing of more auditory-related features or explicit musical features. Our software and trained models, complemented by instructive examples, are available online. 


# Installation

Install the requirements with `pip install -r requirements.txt`. Since ltfatpy is not available on windows, the code can only be used with Linux or Mac.

The datasets used for the experiments are available:

| Dataset       | Type           | Details  |
| ------------- |:-------------| -----|
| [Lakh](https://colinraffel.com/projects/lmd/) | Midi | Used LMD-matched |
| [Maestro](https://magenta.tensorflow.org/datasets/maestro)      |  Midi & piano | Use full dataset |
| [Free Music Archive](https://github.com/mdeff/fma)|    General music | Used only rock song fom fma-small  |


# Instructions

In the folder 'train paper networks' you can find the python scripts we used to train the networks in the paper. To retrain those, just change the dataset folder to where your data is stored.

To train new networks, just run `python train.py --experiment_name awesome_name --data_folder /path/to/your/mp3/or/wav/data/`. We trained GACELA for 7 days on a   NVIDIA Titan pascal X, and the trained models occupy 250Mb. At inference time, GACELA's generator produces a batch of 64 gaps in 14ms.

To test GACELA, either use the `Test GACELA` notebook in the main folder, or use one of the examples provided in the `notebooks` folder.

## Resources

- The paper was published on IEEE Journal of Selected Topics in Signal Processing [IEEE](https://ieeexplore.ieee.org/document/9257074).
- To hear examples please go to the [accompanying website](https://andimarafioti.github.io/GACELA/).

- The checkpoints used for the evaluation of the [paper](https://ieeexplore.ieee.org/document/9257074) can be downloaded [here](https://zenodo.org/record/3897144). Please extract the archives in the folder `saved_results`. Alternatively, you can simply run the script `download_checkpoints.py`:
```
python download_checkpoints.py
```

### Acknowledgments

This project accompanies the research work on audio inpainting of large gaps done at the Acoustics Research Institute in Vienna collaborating with the Swiss Data Science Center. The paper was submitted to an IEEE journal and is under review.

We specially thank Michael Mihocic for running the experiments at the Acoustics Research Institute's laboratory during the coronavirus pandemic as well as the subjects for their participation.
