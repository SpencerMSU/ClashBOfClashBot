package org.example.database.model;

import org.example.cocapi.dto.currentwar.WarAttack;
import org.example.cocapi.dto.currentwar.WarMember;

import java.util.List;
import java.util.Map;

public class WarToSave {
    private final String endTime;
    private final String opponentName;
    private final int teamSize;
    private final int clanStars;
    private final int opponentStars;
    private final double clanDestruction;
    private final double opponentDestruction;
    private final int clanAttacksUsed;
    private final String result;
    private final boolean isCwlWar;
    private final int totalViolations;
    private final Map<WarMember, List<WarAttack>> attacksByMember;

    public WarToSave(String endTime, String opponentName, int teamSize, int clanStars, int opponentStars, double clanDestruction, double opponentDestruction, int clanAttacksUsed, String result, boolean isCwlWar, int totalViolations, Map<WarMember, List<WarAttack>> attacksByMember) {
        this.endTime = endTime;
        this.opponentName = opponentName;
        this.teamSize = teamSize;
        this.clanStars = clanStars;
        this.opponentStars = opponentStars;
        this.clanDestruction = clanDestruction;
        this.opponentDestruction = opponentDestruction;
        this.clanAttacksUsed = clanAttacksUsed;
        this.result = result;
        this.isCwlWar = isCwlWar;
        this.totalViolations = totalViolations;
        this.attacksByMember = attacksByMember;
    }

    // Getters
    public String getEndTime() { return endTime; }
    public String getOpponentName() { return opponentName; }
    public int getTeamSize() { return teamSize; }
    public int getClanStars() { return clanStars; }
    public int getOpponentStars() { return opponentStars; }
    public double getClanDestruction() { return clanDestruction; }
    public double getOpponentDestruction() { return opponentDestruction; }
    public int getClanAttacksUsed() { return clanAttacksUsed; }
    public String getResult() { return result; }
    public boolean isCwlWar() { return isCwlWar; }
    public int getTotalViolations() { return totalViolations; }
    public Map<WarMember, List<WarAttack>> getAttacksByMember() { return attacksByMember; }
}