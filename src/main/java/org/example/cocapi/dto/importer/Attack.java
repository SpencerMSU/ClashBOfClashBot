package org.example.cocapi.dto.importer;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Attack {
    @JsonProperty("opponent_number")
    private int opponentNumber;
    private int stars;
    @JsonProperty("destruction_percentage")
    private String destructionPercentage;

    public Attack() {} // Пустой конструктор (Обязательно!)

    public int getOpponentNumber() { return opponentNumber; }
    public int getStars() { return stars; }
    public String getDestructionPercentage() { return destructionPercentage; }
}