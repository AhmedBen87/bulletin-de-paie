
## Calculation Logic Highlights

*   **Gross Salary:** Sum of all calculated earning components.
*   **Social/Pension Contributions:** Calculated as percentages of the Gross Salary (CNSS base is capped).
*   **Professional Expenses:** Calculated as 20% of (Gross Salary - Total Social/Pension Contributions), capped at 2500 MAD/month. This amount reduces the taxable income.
*   **Net Taxable Income (SNI/RNI):** Gross Salary - Total Social/Pension Contributions - Professional Expenses Deduction.
*   **IGR:** Calculated by annualizing the SNI, applying the official annual tax brackets (rate-minus-deduction method), and dividing the resulting annual tax by 12. **No family charge deductions are applied.**

## Disclaimer

*   This calculator provides an **estimate** for informational purposes only.
*   The calculation is based on standard Moroccan regulations and the specific rates/rules implemented in the code (derived from payslip examples and official guidelines).
*   The **IGR calculation assumes 0 dependents** and does not factor in the family charge deductions provided by law. Therefore, the calculated tax may be higher, and the net salary lower, than for individuals with dependents.
*   Actual net salary on your official payslip may differ due to:
    *   Specific company policies or agreements.
    *   Variations in complementary insurance schemes not included here.
    *   Minor differences in rounding methods used by payroll software.
    *   Specific IGR adjustments or withholdings.
    *   Recent changes in tax laws or contribution rates not yet updated in this tool.
*   **Always refer to your official payslip as the definitive source of information.**

## Future Improvements

*   Add ability to save/load calculation scenarios.
*   Export results to PDF.
*   Include options for more specific complementary insurance plans.
*   Implement user accounts (requires database and security considerations).
*   Develop a mobile application version.
*   Create an API endpoint for fetching current rates/brackets (requires maintenance).
*   Add input for dependents and implement family charge deduction for IGR.

## Contributing

Contributions are welcome! Please feel free to fork the repository, create a feature branch, and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` file for more information (if you choose to add one).
