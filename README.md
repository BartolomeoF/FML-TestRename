# Hi-COLA

Hi-COLA is a package that runs fast, approximate N-body simulations of non-linear structure formation in reduced Horndeski gravity (Horndeski theories with luminal gravitational waves). Hi-COLA is not hard-coded to solve specific Horndeski theories, but is designed to be generic with respect to the reduced Horndeski class. Given an input Lagrangian, Hi-COLA's frontend dynamically constructs the appropriate field equations and consistently solves for the cosmological background, linear growth, and screened fifth force of that theory. This is passed to the backend, an adaptation of the FML library, where a hybrid N-body simulation at significantly reduced computational and temporal cost compared to traditional N-body codes is run. By analysing the particle snapshots, one is able to study the formation of structure through statistics like the matter power spectrum.

See the Documentation folder for guidance on how to install and use Hi-COLA.

Also see [our paper](https://iopscience.iop.org/article/10.1088/1475-7516/2023/03/040) [(pre-print version)](https://arxiv.org/abs/2209.01666), where we detail the work gone into creating Hi-COLA, and the research we have done with it so far.
