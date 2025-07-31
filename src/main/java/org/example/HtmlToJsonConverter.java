package org.example;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

// Основной класс для запуска конвертации
public class HtmlToJsonConverter {

    public static void main(String[] args) {
        // --- ПУТИ К ПАПКАМ (как вы указали) ---
        String htmlsDirectoryPath = "C:\\Users\\SpencerMSU\\Documents\\TG_bots\\ClanBot\\MainPr\\src\\main\\resources\\htmls";
        String outputJsonPath = "C:\\Users\\SpencerMSU\\Documents\\TG_bots\\ClanBot\\MainPr\\src\\main\\resources\\war_data.json";

        File htmlsDir = new File(htmlsDirectoryPath);
        File[] htmlFiles = htmlsDir.listFiles((dir, name) -> name.toLowerCase().endsWith(".html") || name.toLowerCase().endsWith(".mhtml"));

        if (htmlFiles == null || htmlFiles.length == 0) {
            System.out.println("HTML файлы не найдены в директории: " + htmlsDirectoryPath);
            return;
        }

        WarData warData = new WarData();

        // Обрабатываем каждый HTML файл
        for (File file : htmlFiles) {
            try {
                String content = new String(Files.readAllBytes(Paths.get(file.getAbsolutePath())));
                Document doc = Jsoup.parse(content);

                War war = parseWarData(doc);
                if (war != null) {
                    warData.getWars().add(war);
                }

            } catch (IOException e) {
                System.err.println("Ошибка при чтении или парсинге файла " + file.getName() + ": " + e.getMessage());
            }
        }

        // Сохраняем результат в JSON
        saveToJson(warData, outputJsonPath);
        System.out.println("Данные успешно сохранены в " + outputJsonPath);
    }

    /**
     * Парсит основной блок данных о войне из HTML документа.
     * @param doc Parsed Jsoup Document.
     * @return War object.
     */
    private static War parseWarData(Document doc) {
        War war = new War();
        Clan clan1 = new Clan();
        war.setClan1(clan1);

        // --- Извлечение общей информации о войне ---
        Element header = doc.selectFirst("div[data-content=header]");
        if (header != null) {
            war.setSize(getTextFromElement(header, "p.size > span.param-value"));
            war.setDate_start(getTextFromElement(header, "p.date-start > span.param-value"));
            war.setDate_end(getTextFromElement(header, "p.date-end > span.param-value"));
        }

        // --- Извлечение общей статистики КВ ---
        Element resultBlock = doc.selectFirst("div.war-result");
        if (resultBlock != null) {
            war.setTotal_stars(Integer.parseInt(getTextFromElement(resultBlock, "span.clan1.result-stars")));
            war.setDestruction_percentage(getTextFromElement(resultBlock, "span.clan1.result-percent") + "%");
        }

        Element attackProgressionBlock = doc.selectFirst("div.attack-progression");
        if(attackProgressionBlock != null) {
            String used = getTextFromElement(attackProgressionBlock, "div.clan-attack-progression span[data-clan=attacks-count]");
            String max = getTextFromElement(attackProgressionBlock, "div.clan-attack-progression span[data-clan=attacks-max]");
            war.setAttacks_used(used + " / " + max);
        }

        Element resultLabel = doc.selectFirst("p[data-content=result-label]");
        if(resultLabel != null) {
            if(resultLabel.hasClass("result-win")) {
                war.setResult("Victory");
            } else if (resultLabel.hasClass("result-lose")) {
                war.setResult("Defeat");
            } else if (resultLabel.hasClass("result-draw")) {
                war.setResult("Draw");
            }
        }


        // --- Извлечение информации о клане ---
        Element clanElement = doc.selectFirst("div.clan1 a.clan-identity");
        if (clanElement != null) {
            clan1.setName(clanElement.selectFirst("span.clan-name").text());
        }

        // --- Извлечение информации об участниках и их атаках ---
        Elements participantElements = doc.select("div.members-position > div.clan1");
        for (Element participantEl : participantElements) {
            Participant participant = new Participant();

            // Имя участника
            Element nameElement = participantEl.selectFirst("a.player-identity span.player-name");
            if (nameElement != null) {
                participant.setName(nameElement.text());
            } else {
                continue; // Пропускаем, если не нашли имя
            }

            // Атаки участника
            Elements attackElements = participantEl.select("span.members-position-attack");
            for (Element attackEl : attackElements) {
                // Проверяем, что это реальная атака, а не пустой блок
                if (attackEl.selectFirst("a.player-identity") == null) {
                    continue;
                }

                Attack attack = new Attack();

                // Имя оппонента
                attack.setOpponent(getTextFromElement(attackEl, "a.player-identity span.player-name"));
                // Номер оппонента
                attack.setOpponent_number(Integer.parseInt(Objects.requireNonNull(getTextFromElement(attackEl, "span.dot")).trim()));

                // Количество звезд
                int stars = attackEl.select("i.fas.fa-star.stars-win").size();
                attack.setStars(stars);

                // Процент разрушений
                attack.setDestruction_percentage(getTextFromElement(attackEl, "span.attack-percent").replace("%", "").trim() + "%");
                // Длительность атаки
                attack.setDuration(getTextFromElement(attackEl, "span.duration.attack-duration"));

                participant.getAttacks().add(attack);
            }
            clan1.getParticipants().add(participant);
        }
        return war;
    }

    /**
     * Вспомогательный метод для безопасного извлечения текста из элемента.
     * @param element Roditel'skiy element.
     * @param cssQuery CSS-zapros dlya poiska.
     * @return Text soderzhimoye ili pustuyu stroku.
     */
    private static String getTextFromElement(Element element, String cssQuery) {
        Element selected = element.selectFirst(cssQuery);
        return (selected != null) ? selected.text() : "";
    }

    /**
     * Сохраняет объект с данными о войнах в JSON файл.
     * @param warData Ob"yekt s dannymi.
     * @param path Put' k faylu.
     */
    private static void saveToJson(WarData warData, String path) {
        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        try (FileWriter writer = new FileWriter(path)) {
            gson.toJson(warData, writer);
        } catch (IOException e) {
            System.err.println("Ошибка при записи в JSON файл: " + e.getMessage());
        }
    }
}

// --- Классы для структуры JSON ---

class WarData {
    private List<War> wars = new ArrayList<>();

    public List<War> getWars() {
        return wars;
    }
}

class War {
    private String date_start;
    private String date_end;
    private String size;
    private String attacks_used;
    private int total_stars;
    private String destruction_percentage;
    private String result;
    private Clan clan1;

    // Getters and Setters
    public void setDate_start(String date_start) { this.date_start = date_start; }
    public void setDate_end(String date_end) { this.date_end = date_end; }
    public void setSize(String size) { this.size = size.replaceAll("\\s+", " ").trim(); }
    public void setAttacks_used(String attacks_used) { this.attacks_used = attacks_used; }
    public void setTotal_stars(int total_stars) { this.total_stars = total_stars; }
    public void setDestruction_percentage(String destruction_percentage) { this.destruction_percentage = destruction_percentage; }
    public void setResult(String result) { this.result = result; }
    public void setClan1(Clan clan1) { this.clan1 = clan1; }
}

class Clan {
    private String name;
    private List<Participant> participants = new ArrayList<>();

    // Getters and Setters
    public void setName(String name) { this.name = name; }
    public List<Participant> getParticipants() { return participants; }
}

class Participant {
    private String name;
    private List<Attack> attacks = new ArrayList<>();

    // Getters and Setters
    public void setName(String name) { this.name = name; }
    public List<Attack> getAttacks() { return attacks; }
}

class Attack {
    private String opponent;
    private int opponent_number;
    private int stars;
    private String destruction_percentage;
    private String duration;

    // Getters and Setters
    public void setOpponent(String opponent) { this.opponent = opponent; }
    public void setOpponent_number(int opponent_number) { this.opponent_number = opponent_number; }
    public void setStars(int stars) { this.stars = stars; }
    public void setDestruction_percentage(String destruction_percentage) { this.destruction_percentage = destruction_percentage; }
    public void setDuration(String duration) { this.duration = duration; }
}
