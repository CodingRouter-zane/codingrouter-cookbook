import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from calculate import InputError, main, summarize

HEADER = "task_id,currency,total_cost,qualified\n"


class SummaryTests(unittest.TestCase):
    def parse(self, rows):
        return summarize(io.StringIO(HEADER + rows))

    def test_single_currency_includes_failed_task_cost(self):
        result = self.parse("a,CNY,0.1,true\nb,CNY,0.2,false\nc,CNY,0.15,true\n")
        self.assertEqual(result, [{"currency": "CNY", "task_count": 3,
            "qualified_count": 2, "total_cost": "0.450000",
            "cost_per_qualified_result": "0.225000"}])

    def test_currency_groups_are_separate_and_sorted(self):
        result = self.parse("a,USD,1,true\nb,CNY,2,true\nc,USD,3,false\n")
        self.assertEqual([row["currency"] for row in result], ["CNY", "USD"])
        self.assertEqual([row["total_cost"] for row in result], ["2.000000", "4.000000"])
        self.assertEqual([row["qualified_count"] for row in result], [1, 1])

    def test_zero_qualified_is_not_zero_cost(self):
        result = self.parse("a,USD,0.03,false\n")[0]
        self.assertIsNone(result["cost_per_qualified_result"])
        self.assertEqual(result["total_cost"], "0.030000")

    def test_zero_cost_with_qualified_result_is_valid(self):
        self.assertEqual(self.parse("a,CNY,0,true\n")[0]["cost_per_qualified_result"], "0.000000")

    def test_exact_decimal_sum_and_half_up_average(self):
        result = self.parse("a,CNY,0.000001,true\nb,CNY,0,true\n")[0]
        self.assertEqual(result["total_cost"], "0.000001")
        self.assertEqual(result["cost_per_qualified_result"], "0.000001")

    def test_maximum_documented_cost_preserved(self):
        result = self.parse("a,CNY,999999999999.999999,true\n")[0]
        self.assertEqual(result["total_cost"], "999999999999.999999")

    def test_whitespace_trim_and_blank_lines(self):
        self.assertEqual(self.parse("\na, CNY , 0.1 , true \n\n")[0]["task_count"], 1)

    def test_header_reordering_supported(self):
        result = summarize(io.StringIO("currency,task_id,qualified,total_cost\nCNY,a,true,1\n"))
        self.assertEqual(result[0]["total_cost"], "1.000000")

    def test_empty_or_header_only_rejected(self):
        for text in ("", HEADER, HEADER + "\n"):
            with self.subTest(text=text), self.assertRaises(InputError):
                summarize(io.StringIO(text))

    def test_missing_duplicate_and_extra_headers_rejected(self):
        for header in ("task_id,currency,qualified", "task_id,currency,total_cost,total_cost",
                       "task_id,currency,total_cost,qualified,extra"):
            with self.subTest(header=header), self.assertRaises(InputError):
                summarize(io.StringIO(header + "\n"))

    def test_empty_fields_rejected(self):
        for row in (",CNY,1,true", "a,,1,true", "a,CNY,,true", "a,CNY,1,", "a,CNY, ,true"):
            with self.subTest(row=row), self.assertRaises(InputError):
                self.parse(row + "\n")

    def test_missing_and_extra_values_rejected(self):
        for row in ("a,CNY,1", "a,CNY,1,true,extra"):
            with self.subTest(row=row), self.assertRaises(InputError):
                self.parse(row + "\n")

    def test_invalid_costs_rejected(self):
        for cost in ("bad", "-1", "NaN", "Infinity", "-Infinity", "1e2", "+1", ".1",
                     "1.", "0.0000001", "1000000000000", "１２", "1_000"):
            with self.subTest(cost=cost), self.assertRaises(InputError):
                self.parse(f"a,CNY,{cost},true\n")

    def test_invalid_qualified_rejected(self):
        for value in ("yes", "1", "True", "FALSE"):
            with self.subTest(value=value), self.assertRaises(InputError):
                self.parse(f"a,CNY,1,{value}\n")

    def test_currency_format_enforced(self):
        for value in ("cny", "CN", "CNYX", "123", "人民币"):
            with self.subTest(value=value), self.assertRaises(InputError):
                self.parse(f"a,{value},1,true\n")

    def test_duplicate_task_id_across_currencies_rejected(self):
        with self.assertRaisesRegex(InputError, "duplicate task_id"):
            self.parse("a,CNY,1,true\na,USD,1,true\n")


class CliTests(unittest.TestCase):
    def run_main(self, content):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            path.write_bytes(content)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = main([str(path)])
            return code, out.getvalue(), err.getvalue()

    def test_utf8_bom_supported(self):
        code, out, err = self.run_main(("\ufeff" + HEADER + "a,CNY,1,true\n").encode("utf-8"))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)[0]["total_cost"], "1.000000")
        self.assertEqual(err, "")

    def test_invalid_late_row_has_no_partial_output_or_value_echo(self):
        code, out, err = self.run_main((HEADER + "a,CNY,1,true\nb,CNY,PRIVATE_VALUE,false\n").encode())
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("Line 3", err)
        self.assertNotIn("PRIVATE_VALUE", err)

    def test_invalid_utf8_rejected(self):
        code, out, err = self.run_main(b"\xff\xfe")
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("UTF-8", err)

    def test_malformed_csv_rejected(self):
        code, out, err = self.run_main((HEADER + '"unterminated,CNY,1,true').encode())
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("malformed CSV", err)

    def test_missing_file_error_does_not_echo_path(self):
        out, err = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "PRIVATE_PATH.csv")
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = main([path])
        self.assertEqual(code, 2)
        self.assertEqual(out.getvalue(), "")
        self.assertNotIn("PRIVATE_PATH", err.getvalue())

    def test_real_subprocess_sample_and_exit_status(self):
        root = Path(__file__).parent
        result = subprocess.run([sys.executable, str(root / "calculate.py"), str(root / "sample.csv")],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        output = json.loads(result.stdout)
        self.assertEqual(output[0]["cost_per_qualified_result"], "0.225000")
        self.assertIsNone(output[1]["cost_per_qualified_result"])


if __name__ == "__main__":
    unittest.main()
