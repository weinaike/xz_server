package xiaozhi.modules.sys.schedule;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import xiaozhi.common.constant.Constant;
import xiaozhi.modules.sys.service.SysParamsService;
import xiaozhi.modules.sys.utils.DingTalkAlarmUtil;
import xiaozhi.modules.sys.utils.WebSocketValidator;

/**
 * 定期检查 server.websocket 配置的 WebSocket 地址有效性
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class WebSocketHealthCheckTask {
    private final SysParamsService sysParamsService;
    private final DingTalkAlarmUtil dingTalkAlarmUtil;

    /**
     * 每10分钟检查一次 server.websocket 配置的所有地址有效性
     */
    @Scheduled(cron = "0 */10 * * * ?")
    public void checkWebSocketUrls() {
        String wsText = sysParamsService.getValue(Constant.SERVER_WEBSOCKET, true);
        if (StringUtils.isBlank(wsText)) {
            log.warn("[WebSocket健康检查] 未配置 server.websocket");
            return;
        }
        String[] wsUrls = wsText.split("\\;");
        for (String url : wsUrls) {
            boolean valid = WebSocketValidator.validateUrlFormat(url);
            boolean connectable = valid && WebSocketValidator.testConnection(url);
            log.info("[WebSocket健康检查] 地址: {} 格式: {} 可连接: {}", url, valid, connectable);
            if (!connectable) {
                String alarmMsg = String.format("[WebSocket异常告警]\n地址: %s\n格式: %s\n可连接: %s\n请及时检查服务状态！", url, valid, connectable);
                dingTalkAlarmUtil.sendAlarm(alarmMsg);
            }
        }
    }
}
