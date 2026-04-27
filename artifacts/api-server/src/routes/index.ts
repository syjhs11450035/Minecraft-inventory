import { Router, type IRouter } from "express";
import healthRouter from "./health";
import botRouter from "./bot";
import snapshotsRouter from "./snapshots";
import areasRouter from "./areas";
import settingsRouter from "./settings";
import chestPreviewRouter from "./chest-preview";

const router: IRouter = Router();

router.use(healthRouter);
router.use(botRouter);
router.use(snapshotsRouter);
router.use(areasRouter);
router.use(settingsRouter);
router.use(chestPreviewRouter);

export default router;
