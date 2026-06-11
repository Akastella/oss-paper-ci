#include <iostream>

int main() {
    std::cout << "Running analysis..." << std::endl;
    for (int i = 1; i <= 10; i++) {
        std::cout << "  " << i << " -> " << i * i << std::endl;
    }
    std::cout << "Analysis complete." << std::endl;
    return 0;
}
