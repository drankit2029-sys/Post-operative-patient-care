import { useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, BellRing } from "lucide-react";
import { AlertsList } from "./Home";

function useAnimatedNavigate() {
  const navigate = useNavigate();
  const isNavigating = useRef(false);

  const animatedNavigate = (to, delay = 170) => {
    if (isNavigating.current) return;
    isNavigating.current = true;
    setTimeout(() => {
      navigate(to);
    }, delay);
  };

  return animatedNavigate;
}

const pageVariants = {
  initial: { opacity: 0, y: 16 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.35, ease: [0.25, 1, 0.5, 1] },
  },
  exit: {
    opacity: 0,
    y: -12,
    transition: { duration: 0.2, ease: "easeIn" },
  },
};

export default function Alerts() {
  const navigate = useAnimatedNavigate();

  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="max-w-4xl mx-auto px-4 py-8 flex flex-col gap-6"
    >
      {/* Header with Back Navigation */}
      <div className="flex items-center justify-between ">
        <div className="flex items-center gap-3">
          <motion.button
            whileHover={{ scale: 1.08, x: -2 }}
            whileTap={{ scale: 0.9 }}
            transition={{ type: "spring", stiffness: 500, damping: 20 }}
            onClick={() => navigate("/home")}
            className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 shadow-sm transition-colors select-none active:outline-none"
            title="Back to Home"
          >
            <ArrowLeft className="w-5 h-5" />
          </motion.button>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
              System Alerts
              <BellRing className="w-5 h-5 text-indigo-600" />
            </h1>
          </div>
        </div>
      </div>

      {/* Full Alerts List */}
      <AlertsList />
    </motion.div>
  );
}
