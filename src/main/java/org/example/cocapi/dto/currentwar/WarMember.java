package org.example.cocapi.dto.currentwar;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class WarMember {
    private String tag;
    private String name;
    private int mapPosition;
    private List<WarAttack> attacks;

    public String getTag() { return tag; }
    public String getName() { return name; }
    public int getMapPosition() { return mapPosition; }
    public List<WarAttack> getAttacks() { return attacks; }
}