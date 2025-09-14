package org.example.cocapi.dto.currentwar;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class WarClan {
    private String tag;
    private String name;
    private int stars;
    private double destructionPercentage;
    private List<WarMember> members;

    // Getters
    public String getTag() { return tag; }
    public String getName() { return name; }
    public int getStars() { return stars; }
    public double getDestructionPercentage() { return destructionPercentage; }
    public List<WarMember> getMembers() { return members; }
}