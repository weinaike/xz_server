-- 新增ai_agent表字段：agent_template_id、template_version
ALTER TABLE `ai_agent`
  ADD COLUMN `agent_template_id` VARCHAR(64) COMMENT '使用的智能体模板ID' AFTER `birthday`,
  ADD COLUMN `template_version` INT COMMENT '模板版本号' AFTER `agent_template_id`;

-- 新增ai_agent_template表字段：version
ALTER TABLE `ai_agent_template`
  ADD COLUMN `version` INT DEFAULT 100 COMMENT '版本号' AFTER `updated_at`,
  ADD COLUMN `is_default` TINYINT(1) DEFAULT 0 COMMENT '是否为默认模板 0否 1是' AFTER `version`;
