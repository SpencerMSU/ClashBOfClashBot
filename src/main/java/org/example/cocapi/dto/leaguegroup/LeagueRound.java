package org.example.cocapi.dto.leaguegroup;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class LeagueRound {
    private List<String> warTags;
    public List<String> getWarTags() { return warTags; }
}