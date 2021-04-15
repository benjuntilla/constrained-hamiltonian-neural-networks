# Simplifying Hamiltonian and Lagrangian Neural Networks via Explicit Constraints
<p align="center">
  <img src="https://user-images.githubusercontent.com/12687085/94082856-da416d80-fdcf-11ea-8d69-bad3c604c35e.png" width=900>
</p>
This repo contains the implementation and the experiments for the paper 

[Simplifying Hamiltonian and Lagrangian Neural Networks via Explicit Constraints](https://arxiv.org/abs/2010.13581)
by [Marc Finzi](https://mfinzi.github.io/), [Alex Wang](https://keawang.github.io/), and [Andrew Gordon Wilson](https://cims.nyu.edu/~andrewgw/). 


<!-- ![CHNN_perf_summary](https://user-images.githubusercontent.com/12687085/94081992-e75d5d00-fdcd-11ea-9df0-576af6909944.PNG) -->
<!-- ![chaotic_2pendulum](https://user-images.githubusercontent.com/12687085/94081997-e9bfb700-fdcd-11ea-8ca1-ce7ce1cdc717.PNG) -->
<!-- ![systems](https://user-images.githubusercontent.com/12687085/94081999-eb897a80-fdcd-11ea-8e29-c676d4e25f64.PNG) -->

# Some example systems
<img src="assets/5pendulum.gif" width="270"/> <img src="assets/spring2.gif" width="270"/>  <img src="assets/magnet_side.gif" width="270"/> <img src="assets/magnet.gif" width="270"/> <img src="assets/springs5.gif" width="270"/> <img src="assets/racket.gif" width="270"/> 

Each of these animations were produced by running 

```python
from IPython.display import HTML
from biases.systems import ChainPendulum, CoupledPendulum, MagnetPendulum
HTML(CoupledPendulum(3).animate())
```

# Code
Our code in the `biases` directory relies on some publically available codebases which we package together
as a conda environment. [![Code Climate maintainability](https://api.codeclimate.com/v1/badges/a99a88d28ad37a79dbf6/maintainability)](https://codeclimate.com/github/mfinzi/hamiltonian-biases/maintainability) [![ForTheBadge built-with-science](http://ForTheBadge.com/images/badges/built-with-science.svg)](https://xkcd.com/54/)

# Installation instructions
Install PyTorch>=1.0.0

(Optional) Create a wandb account for experiment tracking
## Pip
```bash
git clone https://github.com/mfinzi/constrained-hamiltonian-neural-networks.git
cd constrained-hamiltonian-neural-networks
pip install -e .
```
## Conda
```bash
git clone https://github.com/mfinzi/constrained-hamiltonian-neural-networks.git
cd constrained-hamiltonian-neural-networks
conda env create -f conda_env.yml
pip install ./
```

# Train Models
We have implemented a variety of challenging benchmarks for modeling physical dynamical systems such as ``ChainPendulum``, ``CoupledPendulum``,``MagnetPendulum``,``Gyroscope``,``Rotor`` which can be selected with the ``--body-class`` argument.

<p align="center">
  <img src="https://user-images.githubusercontent.com/12687085/94081999-eb897a80-fdcd-11ea-8e29-c676d4e25f64.PNG" width=1000>
</p>

You can run our models ``CHNN`` and ``CLNN`` as well as the baseline ``NN`` (NeuralODE), ``DeLaN``, and ``HNN`` models with the ``network-class`` argument as shown below.

```
python pl_trainer.py --network-class CHNN --body-class Gyroscope --wandb-project "YOUR WANDB PROJECT"
python pl_trainer.py --network-class CLNN --body-class Gyroscope --wandb-project "YOUR WANDB PROJECT"
python pl_trainer.py --network-class HNN --body-class Gyroscope --wandb-project "YOUR WANDB PROJECT"
python pl_trainer.py --network-class DeLaN --body-class Gyroscope --wandb-project "YOUR WANDB PROJECT"
python pl_trainer.py --network-class NN --body-class Gyroscope --wandb-project "YOUR WANDB PROJECT"
```

Our explicitly constrained ``CHNN`` and ``CLNN`` outperform the competing methods by several orders of magnitude across the different benchmarks as shown below.
<p align="center">
  <img src="https://user-images.githubusercontent.com/12687085/94081992-e75d5d00-fdcd-11ea-9df0-576af6909944.PNG" width=1000>
</p>

If you find our work helpful, please cite it with
```bibtex
@article{finzi2020simplifying,
  title={Simplifying Hamiltonian and Lagrangian Neural Networks via Explicit Constraints},
  author={Finzi, Marc and Wang, Alex and Wilson, Andrew Gordon},
  journal={NeurIPS},
  year={2020}
}
```

