package org.example.cocapi.dto.currentwar;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class WarAttack {
    private String attackerTag;
    private String defenderTag;
    private int stars;
    private int destructionPercentage;
    private int order;

    public String getAttackerTag() { return attackerTag; }
    public String getDefenderTag() { return defenderTag; }
    public int getStars() { return stars; }
    public int getDestructionPercentage() { return destructionPercentage; }
    public int getOrder() { return order; }
}