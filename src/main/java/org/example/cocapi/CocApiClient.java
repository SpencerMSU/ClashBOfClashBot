package org.example.cocapi;

import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.ResponseBody;
import org.example.cocapi.dto.Clan;
import org.example.cocapi.dto.Player;
import org.example.cocapi.dto.WarLog;
import org.example.cocapi.dto.leaguegroup.LeagueGroup;
import org.example.config.BotConfig;
import org.example.cocapi.dto.currentwar.CurrentWar;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.logging.Logger;
import java.util.logging.Level;

/**
 * Client for interacting with the Clash of Clans API.
 * Provides methods to retrieve clan and player information.
 */
public class CocApiClient {
    private static final Logger LOGGER = Logger.getLogger(CocApiClient.class.getName());
    
    private final OkHttpClient client;
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final String API_BASE_URL = "https://api.clashofclans.com/v1";
    
    public CocApiClient() {
        this.client = new OkHttpClient.Builder()
                .connectTimeout(10, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .build();
    }
    
    /**
     * Retrieves current war information for a clan.
     * @param clanTag The clan tag to query
     * @return Current war information if available
     */
    public Optional<CurrentWar> getClanCurrentWar(String clanTag) {
        try {
            String formattedTag = URLEncoder.encode(clanTag, StandardCharsets.UTF_8);
            Request request = new Request.Builder()
                    .url(API_BASE_URL + "/clans/" + formattedTag + "/currentwar")
                    .addHeader("Authorization", "Bearer " + BotConfig.COC_API_TOKEN)
                    .build();

            try (Response response = client.newCall(request).execute()) {
                return handleApiResponse(response, CurrentWar.class, "currentwar");
            }
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error fetching current war for clan: " + clanTag, e);
            return Optional.empty();
        }
    }
    
    /**
     * Retrieves clan war league group information.
     * @param clanTag The clan tag to query
     * @return League group information if available
     */
    public Optional<LeagueGroup> getClanWarLeagueGroup(String clanTag) {
        try {
            String formattedTag = URLEncoder.encode(clanTag, StandardCharsets.UTF_8);
            Request request = new Request.Builder()
                    .url(API_BASE_URL + "/clans/" + formattedTag + "/currentwar/leaguegroup")
                    .addHeader("Authorization", "Bearer " + BotConfig.COC_API_TOKEN)
                    .build();

            try (Response response = client.newCall(request).execute()) {
                return handleApiResponse(response, LeagueGroup.class, "leaguegroup");
            }
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error fetching league group for clan: " + clanTag, e);
            return Optional.empty();
        }
    }
    /**
     * Retrieves player information by player tag.
     * @param playerTag The player tag to query
     * @return Player information if available
     */
    public Optional<Player> getPlayerInfo(String playerTag) {
        try {
            String formattedTag = URLEncoder.encode(playerTag, StandardCharsets.UTF_8);
            Request request = new Request.Builder()
                    .url(API_BASE_URL + "/players/" + formattedTag)
                    .addHeader("Authorization", "Bearer " + BotConfig.COC_API_TOKEN)
                    .build();

            try (Response response = client.newCall(request).execute()) {
                return handleApiResponse(response, Player.class, "player info");
            }
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error fetching player info for: " + playerTag, e);
            return Optional.empty();
        }
    }

    /**
     * Retrieves clan war log.
     * @param clanTag The clan tag to query
     * @return War log if available
     */
    public Optional<WarLog> getClanWarLog(String clanTag) {
        try {
            String formattedTag = URLEncoder.encode(clanTag, StandardCharsets.UTF_8);
            Request request = new Request.Builder()
                    .url(API_BASE_URL + "/clans/" + formattedTag + "/warlog")
                    .addHeader("Authorization", "Bearer " + BotConfig.COC_API_TOKEN)
                    .build();

            try (Response response = client.newCall(request).execute()) {
                return handleApiResponse(response, WarLog.class, "war log");
            }
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error fetching war log for clan: " + clanTag, e);
            return Optional.empty();
        }
    }
    
    /**
     * Retrieves clan information by clan tag.
     * @param clanTag The clan tag to query
     * @return Clan information if available
     */
    public Optional<Clan> getClanInfo(String clanTag) {
        try {
            String formattedTag = URLEncoder.encode(clanTag, StandardCharsets.UTF_8);
            Request request = new Request.Builder()
                    .url(API_BASE_URL + "/clans/" + formattedTag)
                    .addHeader("Authorization", "Bearer " + BotConfig.COC_API_TOKEN)
                    .build();

            try (Response response = client.newCall(request).execute()) {
                return handleApiResponse(response, Clan.class, "clan info");
            }
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error fetching clan info for: " + clanTag, e);
            return Optional.empty();
        }
    }
    
    /**
     * Generic method to handle API responses and parse JSON.
     * @param response The HTTP response
     * @param clazz The target class to deserialize to
     * @param endpoint The endpoint name for logging
     * @return Optional containing the parsed object or empty if error
     */
    private <T> Optional<T> handleApiResponse(Response response, Class<T> clazz, String endpoint) {
        try (ResponseBody body = response.body()) {
            if (response.code() == 403) {
                LOGGER.warning("API key invalid or IP changed for endpoint: " + endpoint);
                return Optional.empty();
            }
            
            // 404 is normal for some endpoints (no war, not in CWL, etc.)
            if (response.code() == 404) {
                LOGGER.info("Resource not found (404) for endpoint: " + endpoint + " - this may be normal");
                return Optional.empty();
            }
            
            if (!response.isSuccessful()) {
                LOGGER.warning("Unsuccessful response for " + endpoint + ": " + response.code() + " " + response.message());
                return Optional.empty();
            }
            
            if (body == null) {
                LOGGER.warning("Empty response body for endpoint: " + endpoint);
                return Optional.empty();
            }
            
            return Optional.of(objectMapper.readValue(body.string(), clazz));
            
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error parsing response for endpoint: " + endpoint, e);
            return Optional.empty();
        }
    }
}