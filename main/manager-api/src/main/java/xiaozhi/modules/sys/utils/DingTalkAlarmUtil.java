package xiaozhi.modules.sys.utils;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import xiaozhi.common.constant.Constant;
import xiaozhi.modules.sys.service.SysParamsService;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

/**
 * 钉钉群机器人告警工具
 */
@Slf4j
@Component
public class DingTalkAlarmUtil {
    // 建议将此URL配置到配置中心或数据库
    private static String webhookUrl = "https://oapi.dingtalk.com/robot/send?access_token=47a515e42482c0e77577e99666680e45176e6ed86700a5c96debdbf2627b64a1";
    private static String secret = "SEC6f4b568bbcf0af6d4d19f5de2cc0571be825dce4423a913c5c8f00514998f02e"; // 可通过配置或setSecret方法设置

    @Autowired(required = false)
    private SysParamsService sysParamsService;

    private void loadConfigFromDb() {
        if (sysParamsService != null) {
            String dbWebhook = sysParamsService.getValue(Constant.DINGTALK_WEBHOOK, true);
            if (dbWebhook != null && !dbWebhook.isEmpty()) {
                webhookUrl = dbWebhook;
            }
            String dbSecret = sysParamsService.getValue(Constant.DINGTALK_SECRET, true);
            if (dbSecret != null && !dbSecret.isEmpty()) {
                secret = dbSecret;
            }
        }
    }

    public static void setWebhookUrl(String url) {
        webhookUrl = url;
    }

    public static void setSecret(String s) {
        secret = s;
    }

    public void sendAlarm(String content) {
        try {
            loadConfigFromDb();
            String url = webhookUrl;
            // 加签处理
            if (secret != null && !secret.isEmpty()) {
                long timestamp = System.currentTimeMillis();
                String stringToSign = timestamp + "\n" + secret;
                Mac mac = Mac.getInstance("HmacSHA256");
                mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
                byte[] signData = mac.doFinal(stringToSign.getBytes(StandardCharsets.UTF_8));
                String sign = URLEncoder.encode(Base64.getEncoder().encodeToString(signData), "UTF-8");
                url += (url.contains("?") ? "&" : "?") + "timestamp=" + timestamp + "&sign=" + sign;
            }
            RestTemplate restTemplate = new RestTemplate();
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            Map<String, Object> msg = new HashMap<>();
            msg.put("msgtype", "text");
            Map<String, Object> text = new HashMap<>();
            text.put("content", content);
            msg.put("text", text);
            Map<String, Object> at = new HashMap<>();
            at.put("isAtAll", true);
            msg.put("at", at);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(msg, headers);
            String resp = restTemplate.postForObject(url, entity, String.class);
            log.info("[钉钉告警] 发送结果: {}", resp);
        } catch (Exception e) {
            log.error("[钉钉告警] 发送失败", e);
        }
    }
}
