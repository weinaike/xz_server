package xiaozhi.modules.agent.service.impl;

import java.util.List;

import org.springframework.stereotype.Service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import xiaozhi.modules.agent.dao.AgentTemplateDao;
import xiaozhi.modules.agent.entity.AgentTemplateEntity;
import xiaozhi.modules.agent.service.AgentTemplateService;

/**
 * @author chenerlei
 * @description 针对表【ai_agent_template(智能体配置模板表)】的数据库操作Service实现
 * @createDate 2025-03-22 11:48:18
 */
@Service
public class AgentTemplateServiceImpl extends ServiceImpl<AgentTemplateDao, AgentTemplateEntity>
        implements AgentTemplateService {

    /**
     * 获取默认模板
     * 
     * @return 默认模板实体
     */
    public AgentTemplateEntity getDefaultTemplate() {
        // 优先查找is_default=1的模板
        LambdaQueryWrapper<AgentTemplateEntity> defaultWrapper = new LambdaQueryWrapper<>();
        defaultWrapper.eq(AgentTemplateEntity::getIsDefault, 1);
        AgentTemplateEntity defaultTemplate = this.getOne(defaultWrapper);
        if (defaultTemplate != null) {
            return defaultTemplate;
        }
        // 若无默认项，按sort排序取第一个
        LambdaQueryWrapper<AgentTemplateEntity> wrapper = new LambdaQueryWrapper<>();
        wrapper.orderByAsc(AgentTemplateEntity::getSort)
                .last("LIMIT 1");
        return this.getOne(wrapper);
    }

    /**
     * 更新默认模板中的模型ID
     * 
     * @param modelType 模型类型
     * @param modelId   模型ID
     */
    @Override
    public void updateDefaultTemplateModelId(String modelType, String modelId) {
        modelType = modelType.toUpperCase();

        UpdateWrapper<AgentTemplateEntity> wrapper = new UpdateWrapper<>();
        switch (modelType) {
            case "ASR":
                wrapper.set("asr_model_id", modelId);
                break;
            case "VAD":
                wrapper.set("vad_model_id", modelId);
                break;
            case "LLM":
                wrapper.set("llm_model_id", modelId);
                break;
            case "TTS":
                wrapper.set("tts_model_id", modelId);
                wrapper.set("tts_voice_id", null);
                break;
            case "MEMORY":
                wrapper.set("mem_model_id", modelId);
                break;
            case "INTENT":
                wrapper.set("intent_model_id", modelId);
                break;
        }
        wrapper.ge("sort", 0);
        update(wrapper);
    }

    /**
     * 清除默认模板
     */
    public void clearDefaultTemplate() {
        // 先查找所有 is_default != 0 的模板
        LambdaQueryWrapper<AgentTemplateEntity> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.ne(AgentTemplateEntity::getIsDefault, 0);
        List<AgentTemplateEntity> defaultTemplates = this.list(queryWrapper);
        if (defaultTemplates != null && !defaultTemplates.isEmpty()) {
            for (AgentTemplateEntity template : defaultTemplates) {
                template.setIsDefault(0);
                this.updateById(template);
            }
        }
    }
}
