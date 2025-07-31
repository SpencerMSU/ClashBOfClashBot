package org.example.database.model;

// Простой класс для хранения данных об одной атаке из нашей БД
public class AttackData {
    private final String attackerName;
    private final int stars;
    private final double destruction;

    public AttackData(String attackerName, int stars, double destruction) {
        this.attackerName = attackerName;
        this.stars = stars;
        this.destruction = destruction;
    }

    public String getAttackerName() { return attackerName; }
    public int getStars() { return stars; }
    public double getDestruction() { return destruction; }
}