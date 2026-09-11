# Roadmap

1. Expand faithful logical MuTA validation and reproduce more published tasks.
   Implement tied measurement groups, bounds, mixed quantum inputs, noisier
   resource branches and the learned teleportation instrument. Independently
   train the pinned MentPy reference, rather than compare only checkpoints.
2. Specify and validate GKP logical measurement/injection instruments,
   a decoder with explicit leakage and failure outcomes, correlated input
   preparation, and separate cutoff, grid, peak, envelope and energy studies.
   Only then enable general `representation="gkp"` forward execution.
3. Derive and implement CVMuTA independently. Prove the ideal cell map,
   characterize its finite-resource channel, establish identity embeddings in
   the appropriate regime, and validate against direct PhotoGraphiQ physics.
4. Expand training with valid autodiff, stochastic estimators, mini-batches,
   noise-aware readouts, callbacks and optimizer/model checkpointing.
5. Complete full paper reproduction, ten larger demo projects and the full
   release acceptance checklist. Run the Python CI matrix on hosted runners.

Reservoir computing and recurrent models are future directions. None of these
items imply quantum advantage or an error-correction threshold.
