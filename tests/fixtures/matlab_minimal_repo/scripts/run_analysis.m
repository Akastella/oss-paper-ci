% Main analysis script
rng(42);
fprintf('Running analysis...\n');
x = randn(100, 1);
y = 2*x + randn(100, 1);
save('results/analysis.mat', 'x', 'y');
fprintf('Done.\n');