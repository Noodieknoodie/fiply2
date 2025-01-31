.cursor/rules/PROJECT_OVERVIEW.md

# This document is a high-level overview of the FIPLI project

################ FIPLI: System Overview & Core Modeling #################

# Core Purpose & High-Level Overview

Fipli is a streamlined financial planning projection system implementing deterministic linear modeling. Conceptually, it's similar to eMoney or MoneyGuidePro, but with an intentionally simplified computational model. While the original prototype was built in Excel, the current implementation uses Python for computational logic and SQL for data persistence, though the core algorithms could be implemented in either environment. Fipli is optimized for scenario analysis and comparative projection modeling rather than granular financial planning - we explicitly exclude tax implications, withdrawal sequencing, and other complexities typically found in comprehensive financial planning tools.

# The Fundamental Visualization

The core visualization model is a line graph where the Y-axis represents portfolio value in dollars and the X-axis tracks time progression in years. The X-axis is structured around absolute years (e.g., 2025, 2026, 2027) rather than relative age. However, since age is directly tied to the selected start year and date of birth, projections maintain full compatibility with both age-based and year-based perspectives. The tick marks represent annual periods, initiating from the year the plan was created, ensuring a fixed and consistent starting point for projections. The fundamental design principle is strict adherence to annual-period linear projections - we explicitly avoid any intra-year calculations or display granularity. The line itself represents the projected retirement portfolio value - specifically the retirement nest egg, not total net worth.

# Data Model Foundation

The composition of this nest egg is determined through a structured set of user-defined inputs. These inputs encompass several core data entities: assets, liabilities, scheduled inflows, scheduled outflows, and retirement income streams. Each of these entities can be organized into user-defined classification buckets - for instance, assets might be categorized as qualified or non-qualified, while liabilities might be grouped into personal or business categories. The system is governed by a set of base parameters called base facts, which include the default growth rate, inflation rate, and time period boundaries (start, retirement, and end points expressed in absolute years). It's important to note that retirement spending, while central to the analysis, is intentionally excluded from these base facts.

# Growth Rate System

The growth rate system in Fipli is particularly sophisticated. The base facts establish a default growth rate, but individual assets can override this in several ways. An asset can have a simple growth rate override - useful for assigning different returns to different investment types, like setting a higher growth rate for an aggressive equity portfolio. For more complex projections, assets can use stepwise growth rate overrides, where different rates apply during different time periods. When using stepwise overrides, any time periods not explicitly covered default back to the scenario's (or base facts') default growth rate. Liabilities follow a different model - they don't participate in the default growth rate system at all, instead having an optional interest rate parameter that, if specified, determines liability growth. Inflation adjustments can be toggled for various inputs, including scheduled inflows, scheduled outflows, and retirement income streams. When enabled, these values are adjusted before they are applied in the annual calculations. When enabled, these values are automatically adjusted using the inflation rate specified in either the base facts or scenario assumptions.

# Scenario System

Each scenario begins as a clone of the base facts, creating a sandbox for "what-if" analysis. While scenarios inherit all base fact parameters, they can independently override any of these values. What makes scenarios particularly powerful is their unique retirement spending parameter - an inflation-adjusted annual outflow that begins at retirement and continues through the final projection year. To clarify the distinction between scheduled flows and retirement spending: the scheduled inflows and outflows in the base facts are meant for modeling discrete events like education expenses or inheritance receipts. This allows users to quickly test different spending levels against their base assumptions. Often, users will use scenarios to solve for maximum sustainable spending - essentially finding the spending level that depletes the portfolio exactly at the final projection year - but the tool supports any arbitrary spending pattern.

# Business Logic & Calculations

The business logic enforces consistent date handling throughout the system. We follow a "enter what you know, calculate what you need" principle. Users enter their date of birth, and the system derives their current age dynamically. However, all projections and calculations are stored in absolute years to maintain a unified and consistent timeline. The system ensures full interchangeability between age and year for all inputs, calculations, and visualizations. Users can input values using either format, and the system dynamically converts between them as needed. Scheduled inflows and outflows are expressed in years, while retirement income streams default to age-based inputs, as retirement benefits typically trigger at specific ages. All calculations happen dynamically, with the system aggregating assets, applying growth rates, processing scheduled flows, and computing portfolio values in a way that maintains consistency with standard financial planning practices while keeping the computational model straightforward and deterministic.​​​​​​​​​​​​​​​​

