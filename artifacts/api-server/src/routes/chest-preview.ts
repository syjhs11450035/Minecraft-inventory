import { Router, type IRouter } from "express";
import { previewChest } from "../lib/chest-preview";

const router: IRouter = Router();

router.post("/chest/preview", async (req, res) => {
  const x = req.body?.x;
  const y = req.body?.y;
  const z = req.body?.z;
  const range = req.body?.range;
  try {
    const result = await previewChest({
      x: typeof x === "number" ? x : null,
      y: typeof y === "number" ? y : null,
      z: typeof z === "number" ? z : null,
      range: typeof range === "number" ? range : undefined,
    });
    res.json({ ok: true, ...result });
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

export default router;
