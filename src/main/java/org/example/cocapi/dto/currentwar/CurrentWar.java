package org.example.cocapi.dto.currentwar;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class CurrentWar {
    private String state; // "inWar", "preparation", "warEnded"
    private String startTime; // <-- НЕДОСТАЮЩЕЕ ПОЛЕ
    private String endTime;
    private WarClan clan;
    private WarClan opponent;

    // Getters
    public String getState() { return state; }
    public String getStartTime() { return startTime; } // <-- НЕДОСТАЮЩИЙ МЕТОД
    public String getEndTime() { return endTime; }
    public WarClan getClan() { return clan; }
    public WarClan getOpponent() { return opponent; }
}