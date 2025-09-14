package org.example.cocapi.dto.currentwar;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class CurrentWar {
    private String state;
    private String startTime;
    private String endTime;
    private int teamSize; // Добавлено
    private int attacksPerMember; // Добавлено
    private WarClan clan;
    private WarClan opponent;

    // Getters
    public String getState() { return state; }
    public String getStartTime() { return startTime; }
    public String getEndTime() { return endTime; }
    public int getTeamSize() { return teamSize; }
    public int getAttacksPerMember() { return attacksPerMember; }
    public WarClan getClan() { return clan; }
    public WarClan getOpponent() { return opponent; }
}