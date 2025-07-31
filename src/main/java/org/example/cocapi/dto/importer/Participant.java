package org.example.cocapi.dto.importer;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Participant {
    private String name;
    private List<Attack> attacks;

    public Participant() {} // Пустой конструктор (Обязательно!)

    public String getName() { return name; }
    public List<Attack> getAttacks() { return attacks; }
}