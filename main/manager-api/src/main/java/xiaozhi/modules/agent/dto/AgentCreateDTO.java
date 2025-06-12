package xiaozhi.modules.agent.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.io.Serializable;

/**
 * 智能体创建DTO
 * 专用于新增智能体，不包含id、agentCode和sort字段，这些字段由系统自动生成/设置默认值
 */
@Data
@Schema(description = "智能体创建对象")
public class AgentCreateDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    @Schema(description = "智能体名称", example = "客服助手")
    @NotBlank(message = "智能体名称不能为空")
    private String agentName;

    @Schema(description = "小主名称")
    @NotBlank(message = "小主名称不能为空")
    private String nickName;

    @Schema(description = "性别1男，2女，0保密", example = "0")
    @NotBlank(message = "性别不能为空")
    @Size(min = 1, max = 1, message = "性别只能是0保密，1男，2女")
    private String sex;

    @Schema(description = "生日", format = "yyyymmdd")
    @NotBlank(message = "生日不能为空")
    @Size(min = 10, max = 10, message = "生日的格式是yyyyMMdd")
    private String birthday;

    @Schema(description = "智能体模板ID", example = "123456")
    // @NotBlank(message = "智能体模板ID不能为空")
    private String agentTemplateId;
}