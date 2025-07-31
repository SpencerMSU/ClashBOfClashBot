package org.example.cocapi.dto.importer;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public class WarData {
    @JsonProperty("date_end")
    private String dateEnd;
    private String size;
    private String result;
    @JsonProperty("total_stars")
    private int totalStars;
    @JsonProperty("attacks_used")
    private String attacksUsed;
    @JsonProperty("destruction_percentage")
    private String destructionPercentage;
    private ClanDetails clan1;
    private ClanDetails clan2; // Добавим, чтобы импортер не падал, если поле появится

    // Конструкторы для разных ситуаций
    public WarData() {}

    public WarData(String dateEnd, String opponentName, String size, String result) {
        this.dateEnd = dateEnd;
        this.size = size;
        this.result = result;
        this.clan1 = new ClanDetails(opponentName);
    }

    public WarData(String dateEnd, String opponentName, String size, String result, int clanStars, double clanDestruction, int clanAttacksUsed, int opponentStars, double opponentDestruction) {
        this.dateEnd = dateEnd;
        this.size = size;
        this.result = result;
        this.clan1 = new ClanDetails("Русские\"", clanStars, clanDestruction, clanAttacksUsed);
        this.clan2 = new ClanDetails(opponentName, opponentStars, opponentDestruction, 0);
    }

    // Getters
    public String getDateEnd() { return dateEnd; }
    public String getSize() { return size; }
    public String getResult() { return result; }
    public int getTotalStars() { return totalStars; }
    public String getAttacksUsed() { return attacksUsed; }
    public String getDestructionPercentage() { return destructionPercentage; }
    public ClanDetails getClan1() { return clan1; }
    public ClanDetails getClan2() { return clan2; }
}