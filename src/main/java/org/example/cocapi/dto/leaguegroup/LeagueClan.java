package org.example.cocapi.dto.leaguegroup;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class LeagueClan {
    private String tag;
    private String name;

    public String getTag() { return tag; }
    public String getName() { return name; }
}