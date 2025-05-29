-- 新增ai_agent表字段：小主名称、性别、生日
ALTER TABLE `ai_agent`
  ADD COLUMN `nick_name` VARCHAR(64) COMMENT '小主名称' AFTER `updated_at`,
  ADD COLUMN `sex` VARCHAR(8) COMMENT '性别1男，2女，0保密' AFTER `nick_name`,
  ADD COLUMN `birthday` VARCHAR(16) COMMENT '生日' AFTER `sex`;
