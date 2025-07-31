package org.example.cocapi.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Player {
    private String tag;
    private String name;
    private int townHallLevel;
    private int expLevel;
    private int trophies;
    private int warStars;
    private ClanInfo clan;
    // Новые поля для Деревни Строителя
    private int builderHallLevel;
    private int versusTrophies;

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ClanInfo {
        private String tag;
        private String name;

        public String getTag() { return tag; }
        public void setTag(String tag) { this.tag = tag; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
    }

    // Getters & Setters
    public String getTag() { return tag; }
    public void setTag(String tag) { this.tag = tag; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getTownHallLevel() { return townHallLevel; }
    public void setTownHallLevel(int townHallLevel) { this.townHallLevel = townHallLevel; }
    public int getExpLevel() { return expLevel; }
    public void setExpLevel(int expLevel) { this.expLevel = expLevel; }
    public int getTrophies() { return trophies; }
    public void setTrophies(int trophies) { this.trophies = trophies; }
    public int getWarStars() { return warStars; }
    public void setWarStars(int warStars) { this.warStars = warStars; }
    public ClanInfo getClan() { return clan; }
    public void setClan(ClanInfo clan) { this.clan = clan; }
    public int getBuilderHallLevel() { return builderHallLevel; }
    public void setBuilderHallLevel(int builderHallLevel) { this.builderHallLevel = builderHallLevel; }
    public int getVersusTrophies() { return versusTrophies; }
    public void setVersusTrophies(int versusTrophies) { this.versusTrophies = versusTrophies; }
}