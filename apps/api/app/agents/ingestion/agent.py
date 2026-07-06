from app.domain.documents.schemas import DocumentUploadResult
from app.workflows.ingestion_workflow import IngestionWorkflow, IngestionWorkflowInput


class IngestionAgent:
    def __init__(self) -> None:
        self.workflow = IngestionWorkflow()

    async def run(self, workflow_input: IngestionWorkflowInput) -> DocumentUploadResult:
        return await self.workflow.run(workflow_input)

