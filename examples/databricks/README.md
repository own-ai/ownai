# Databricks

The [Databricks](https://www.databricks.com/) Lakehouse Platform unifies data, analytics, and AI on one platform.

## Prerequisites

- An LLM was registered and deployed to [a Databricks serving endpoint](https://docs.databricks.com/machine-learning/model-serving/index.html).
- You have ["Can Query" permission](https://docs.databricks.com/security/auth-authz/access-control/serving-endpoint-acl.html) to the endpoint.

## Set up

To use these AIs, you should set the environment variables `DATABRICKS_HOST` and `DATABRICKS_API_TOKEN` (e.g. in your server's `.env` file).
Then download the aifile and load it with ownAI (in ownAI, click on the logo in the upper left corner to open the menu, then select "AI Workshop", then "New AI" and "Load Aifile").

## Privacy

Your models are running on an external provider's infrastructure. Please refer to the provider's privacy policy for details.
