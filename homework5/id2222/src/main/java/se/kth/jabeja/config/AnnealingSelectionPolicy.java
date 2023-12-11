package se.kth.jabeja.config;

public enum AnnealingSelectionPolicy {
    LINEAR("LINEAR"),
    EXPONENTIAL("EXPONENTIAL"),
    IMPROVED_EXP("IMPROVED_EXP");

    String name;

    AnnealingSelectionPolicy(String name) {
        this.name = name;
    }

    @Override
    public String toString() {
        return name;
    }
}