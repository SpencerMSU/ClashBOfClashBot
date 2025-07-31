package org.example.cocapi.dto.importer;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class ClanDetails {
    private String name;
    private int stars;
    @JsonProperty("destruction_percentage")
    private double destructionPercentage;
    @JsonProperty("attacks_used")
    private int attacksUsed;
    private List<Participant> participants;

    public ClanDetails() {}
    public ClanDetails(String name) { this.name = name; }
    public ClanDetails(String name, int stars, double destructionPercentage, int attacksUsed) {
        this.name = name;
        this.stars = stars;
        this.destructionPercentage = destructionPercentage;
        this.attacksUsed = attacksUsed;
    }

    // Getters
    public String getName() { return name; }
    public int getStars() { return stars; }
    public double getDestructionPercentage() { return destructionPercentage; }
    public int getAttacksUsed() { return attacksUsed; }
    public List<Participant> getParticipants() { return participants; }
}