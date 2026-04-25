import { Router, type IRouter } from "express";
import healthRouter from "./health";
import botRouter from "./bot";
import snapshotsRouter from "./snapshots";
import areasRouter from "./areas";

const router: IRouter = Router();

router.use(healthRouter);
router.use(botRouter);
router.use(snapshotsRouter);
router.use(areasRouter);

export default router;
