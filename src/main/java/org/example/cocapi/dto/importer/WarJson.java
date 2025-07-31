package org.example.cocapi.dto.importer;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class WarJson {
    private List<WarData> wars;

    public WarJson() {} // Пустой конструктор

    public List<WarData> getWars() { return wars; }
}