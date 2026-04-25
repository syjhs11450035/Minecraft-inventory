import { Router, type IRouter } from "express";
import healthRouter from "./health";
import botRouter from "./bot";
import snapshotsRouter from "./snapshots";

const router: IRouter = Router();

router.use(healthRouter);
router.use(botRouter);
router.use(snapshotsRouter);

export default router;
