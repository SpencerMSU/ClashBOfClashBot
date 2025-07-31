package org.example.cocapi;

import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import org.example.cocapi.dto.Clan;
import org.example.cocapi.dto.Player;
import org.example.cocapi.dto.WarLog;
import org.example.cocapi.dto.leaguegroup.LeagueGroup;
import org.example.config.BotConfig;
import org.example.cocapi.dto.WarLog;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Optional;
import org.example.cocapi.dto.currentwar.CurrentWar;
public class CocApiClient {
    private final OkHttpClient client = new OkHttpClient();
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final String API_BASE_URL = "https://api.clashofclans.com/v1";
    public Optional<CurrentWar> getClanCurrentWar(String clanTag) {
        try {
            String formattedTag = URLEncoder.encode(clanTag, StandardCharsets.UTF_8);
            Request request = new Request.Builder()
                    .url(API_BASE_URL + "/clans/" + formattedTag + "/currentwar")
                    .addHeader("Authorization", "Bearer " + BotConfig.COC_API_TOKEN)
                    .build();

            try (Response response = client.newCall(request).execute()) {
                if (response.code() == 403) {
                    System.err.println("ОШИБКА 403 (currentwar): API ключ недействителен или ваш IP изменился.");
                    return Optional.empty();
                }
                // Ошибка 404 означает "не в войне", это не ошибка, а нормальное состояние
                if (response.code() == 404) {
                    return Optional.empty();
                }
                if (!response.isSuccessful()) {
                    System.err.println("Ошибка при запросе currentwar: " + response.code());
                    return Optional.empty();
                }
                return Optional.of(objectMapper.readValue(response.body().string(), CurrentWar.class));
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Optional.empty();
        }
    }
    public Optional<LeagueGroup> getClanWarLeagueGroup(String clanTag) {
        try {
            String formattedTag = URLEncoder.encode(clanTag, StandardCharsets.UTF_8);
            Request request = new Request.Builder()
                    .url(API_BASE_URL + "/clans/" + formattedTag + "/currentwar/leaguegroup")
                    .addHeader("Authorization", "Bearer " + BotConfig.COC_API_TOKEN)
                    .build();

            try (Response response = client.newCall(request).execute()) {
                if (response.code() == 403) {
                    System.err.println("ОШИБКА 403 (leaguegroup): API ключ недействителен или ваш IP изменился.");
                    return Optional.empty();
                }
                // Ошибка 404 означает "не в ЛВК", это не ошибка
                if (response.code() == 404) {
                    return Optional.empty();
                }
                if (!response.isSuccessful()) {
                    System.err.println("Ошибка при запросе leaguegroup: " + response.code());
                    return Optional.empty();
                }
                return Optional.of(objectMapper.readValue(response.body().string(), LeagueGroup.class));
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Optional.empty();
        }
    }
    public Optional<Player> getPlayerInfo(String playerTag) {
        try {
            String formattedTag = URLEncoder.encode(playerTag, StandardCharsets.UTF_8);
            Request request = new Request.Builder()
                    .url(API_BASE_URL + "/players/" + formattedTag)
                    .addHeader("Authorization", "Bearer " + BotConfig.COC_API_TOKEN)
                    .build();

            try (Response response = client.newCall(request).execute()) {
                // Улучшенная обработка ошибок
                if (response.code() == 403) {
                    System.err.println("ОШИБКА 403: API ключ недействителен или ваш IP изменился. Проверьте настройки на developer.clashofclans.com");
                    return Optional.empty();
                }
                if (!response.isSuccessful()) {
                    return Optional.empty();
                }
                return Optional.of(objectMapper.readValue(response.body().string(), Player.class));
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Optional.empty();
        }
    }

    public Optional<WarLog> getClanWarLog(String clanTag) {
        try {
            String formattedTag = URLEncoder.encode(clanTag, StandardCharsets.UTF_8);
            Request request = new Request.Builder()
                    .url(API_BASE_URL + "/clans/" + formattedTag + "/warlog")
                    .addHeader("Authorization", "Bearer " + BotConfig.COC_API_TOKEN)
                    .build();

            try (Response response = client.newCall(request).execute()) {
                if (response.code() == 403) {
                    System.err.println("ОШИБКА 403: Журнал войн закрыт или API ключ недействителен.");
                    return Optional.empty();
                }
                if (!response.isSuccessful()) return Optional.empty();
                return Optional.of(objectMapper.readValue(response.body().string(), WarLog.class));
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Optional.empty();
        }
    }
    public Optional<Clan> getClanInfo(String clanTag) {
        try {
            String formattedTag = URLEncoder.encode(clanTag, StandardCharsets.UTF_8);
            Request request = new Request.Builder()
                    .url(API_BASE_URL + "/clans/" + formattedTag)
                    .addHeader("Authorization", "Bearer " + BotConfig.COC_API_TOKEN)
                    .build();

            try (Response response = client.newCall(request).execute()) {
                // Улучшенная обработка ошибок
                if (response.code() == 403) {
                    System.err.println("ОШИБКА 403: API ключ недействителен или ваш IP изменился. Проверьте настройки на developer.clashofclans.com");
                    return Optional.empty();
                }
                if (!response.isSuccessful()) {
                    return Optional.empty();
                }
                return Optional.of(objectMapper.readValue(response.body().string(), Clan.class));
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Optional.empty();
        }
    }
}