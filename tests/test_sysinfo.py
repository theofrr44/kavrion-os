import os, sys, time, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "config", "includes.chroot", "usr", "lib", "kavrion"))
import kavrion_sysinfo as s


class Parsing(unittest.TestCase):
    def test_cpu(self):
        self.assertEqual(s.parse_cpu_times("cpu  10 0 10 70 10 0 0 0 0 0\ncpu0 1 1 1 1"), (100, 80))

    def test_meminfo(self):
        m = s.parse_meminfo("MemTotal: 4096 kB\nMemAvailable: 1024 kB\nSwapTotal: 100 kB\nSwapFree: 40 kB")
        self.assertEqual((m["total"], m["used"], m["swap_used"]), (4096 * 1024, 3072 * 1024, 60 * 1024))

    def test_net_ignores_lo(self):
        t = "h1\nh2\n  lo: 5 0 0 0 0 0 0 0 5 0\neth0: 100 0 0 0 0 0 0 0 200 0"
        self.assertEqual(s.parse_net_dev(t), {"eth0": (100, 200)})

    def test_proc_stat_name_with_spaces(self):
        f = " ".join(["S"] + ["0"] * 10 + ["7", "3"] + ["0"] * 8 + ["42"])
        self.assertEqual(s.parse_proc_stat("123 (my (weird) app) " + f), ("my (weird) app", "S", 10, 42))

    def test_human(self):
        self.assertEqual(s.human(1536), "1.5 Ko")

    def test_duration(self):
        self.assertEqual(s.fmt_duration(90061), "1j 1h 01min")


@unittest.skipUnless(os.path.exists("/proc/stat"), "Linux requis")
class Live(unittest.TestCase):
    def test_sampler_real_data(self):
        sm = s.Sampler()
        sm.sample()
        sum(i * i for i in range(300000))
        time.sleep(0.3)
        d = sm.sample()
        self.assertTrue(0 <= d["cpu_percent"] <= 100)
        self.assertGreater(d["mem"]["total"], 0)
        self.assertGreater(d["process_count"], 0)
        self.assertIn(os.getpid(), [p["pid"] for p in sm.sample(top=100000)["processes"]])
        self.assertIsInstance(d["temps"], list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
