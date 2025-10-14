/*
    This SQL query retrieves distinct organization codes, names, regions, NHSE organization types, 
    ICB codes, and ICB names from the ODS schema. It filters for active organizations that have 
    associated device records in the last 12 months of the PLCM Devices data.
    For security and obscuration, the schema and table names are placeholders and should be replaced 
    with actual values in the environment where this query is executed.
*/
SELECT DISTINCT
    [ORG].[OrgId_extension] AS Org_Code,
    [ORG].[Name] AS Org_Name,
    [HIER].[Region_Name] AS Region,
    [HIER].[NHSE_Organisation_Type] AS NHSE_Org_Type,
    [HIER].[ICB_Code] AS ICB_Code,
    [HIER].[Integrated_Care_Board_Name] AS ICB_Name
FROM
    [{ods_schema_placeholder}].[{org_ods_table_placeholder}] [ORG] WITH(NOLOCK)
    LEFT JOIN [{ods_schema_placeholder}].[{hierarchies_ods_table_placeholder}] [HIER] WITH(NOLOCK) 
        ON [ORG].[OrgId_extension] = [HIER].[Organisation_Code]
WHERE
    [ORG].[Is_Latest] = 1
    AND [ORG].[Status] = 'Active'
    AND EXISTS (
        SELECT 1 
        FROM [{report_schema_placeholder}].[{curated_devices_placeholder}] [DEV] 
        WHERE [DEV].[Der_Provider_Code] = [ORG].[OrgId_extension]
    )
ORDER BY [Org_Code];