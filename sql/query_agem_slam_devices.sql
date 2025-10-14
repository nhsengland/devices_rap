/*
    This SQL query retrieves the last 12 months of device records from the PLCM Devices data.
    I similar script is ran monthly to create the curated devices table.
    For security and obscuration, the schema and table names are placeholders and should be replaced
    with actual values in the environment where this query is executed.
*/

SELECT DISTINCT
	[Devices_ident],
	[CLN_Activity_Month],
	[CLN_Activity_Year],
	[CLN_Device_Insertion_Date],
	[CLN_Purchased_Device_Contract],
	[CLN_Manufacturer],
	[CLN_Manufacturer_Device_Name],
	[CLN_Device_Serial_Number],
	[CLN_Size],
	[CLN_Quantity],
	[CLN_Supplier_Unit_Price],
	[CLN_Commissioner_Unit_Price],
	[CLN_VAT_Charged],
	[CLN_Total_Cost],
	[Der_Provider_Code],
	[CLN_Commissioner_Code],
	[Der_Commissioner_Code],
	[Der_NHSE_ServiceCategory],
	[Der_NHSE_ServiceLine],
	[Der_GP_Practice_Code],
	[Der_High_Level_Device_Type],
	[Der_Subsidiary_Device_Type],
	[Der_Purchased_Device_Contract],
	[Der_VAT_Charged],
	[CLN_High_Level_Device_Type],
	[RAW_Attendance_Identifier],
	[CLN_Attendance_Identifier],
	[RAW_Created_Datetime]
FROM
	[{devices_schema_placeholder}].[{devices_table_placeholder}] [D]
	LEFT JOIN
		(
			SELECT
				[DER_Activity_Period],
                ROW_NUMBER() OVER (ORDER BY [DER_Activity_Period] DESC) AS [Order]
			FROM
				(
					SELECT DISTINCT
						[DER_Activity_Period]
					FROM
						[{devices_schema_placeholder}].[{devices_table_placeholder}]
				) a
		) [O] ON [D].[DER_Activity_Period] = [O].[DER_Activity_Period]
WHERE
	[O].[Order] BETWEEN 1 AND 12
ORDER BY
	3 DESC,2 DESC