# Main analysis script
library(ggplot2)
library(dplyr)

set.seed(42)

# Load data
data <- read.csv("data/results.csv")

# Generate figure
p <- ggplot(data, aes(x = x, y = y)) + geom_point()
ggsave("figures/plot.png", p)

cat("Analysis complete\n")