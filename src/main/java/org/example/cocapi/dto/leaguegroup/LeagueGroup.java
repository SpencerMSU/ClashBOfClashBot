package org.example.cocapi.dto.leaguegroup;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class LeagueGroup {
    private String state;
    private String season;
    private List<LeagueClan> clans;
    private List<LeagueRound> rounds;

    public String getState() { return state; }
    public String getSeason() { return season; }
    public List<LeagueClan> getClans() { return clans; }
    public List<LeagueRound> getRounds() { return rounds; }
}