// 研究分支元数据
// 与 config/topics.yaml 保持一致；V1 仅 vision_force 为 active

export interface TopicMeta {
  id: string;
  name_zh: string;
  name_en: string;
  nav_label: string;
  status: "active" | "coming_soon";
  description_zh: string;
}

export const TOPICS: TopicMeta[] = [
  {
    id: "vision_force",
    name_zh: "视觉力觉融合",
    name_en: "Vision-Force Fusion",
    nav_label: "Vision-Force Fusion",
    status: "active",
    description_zh: "RGB/RGB-D 视觉与末端六维力/力矩传感器融合的机器人操作研究。",
  },
  {
    id: "failure_understanding",
    name_zh: "失败理解",
    name_en: "Failure Understanding",
    nav_label: "Failure Understanding",
    status: "coming_soon",
    description_zh: "任务成功预测、失败检测、进度估计、运行时监控等。",
  },
  {
    id: "failure_recovery",
    name_zh: "失败恢复",
    name_en: "Failure Recovery",
    nav_label: "Failure Recovery",
    status: "coming_soon",
    description_zh: "重试、重规划、纠错动作、恢复策略、分层恢复等。",
  },
  {
    id: "vla_manipulation",
    name_zh: "VLA 与操作",
    name_en: "VLA & Manipulation",
    nav_label: "VLA & Manipulation",
    status: "coming_soon",
    description_zh: "Vision-Language-Action、通用机器人策略、模仿学习等。",
  },
  {
    id: "generative_policy",
    name_zh: "生成式策略",
    name_en: "Generative Policy",
    nav_label: "Generative Policy",
    status: "coming_soon",
    description_zh: "Diffusion Policy、Flow Matching、生成式机器人策略等。",
  },
];

export const ACTIVE_TOPIC = TOPICS.find((t) => t.status === "active")!;
