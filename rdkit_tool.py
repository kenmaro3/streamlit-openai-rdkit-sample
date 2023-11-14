from langchain.tools.base import BaseTool
import pubchempy as pcp

class RDKitTool(BaseTool):
    name = "RDKitTool"
    description = (
        "This tool is useful to get the SMILES of chemical compaund."
        "Input should be a chemical compound name string. Chemical compound name should be written in English."
    )

    def _run(self, compound_name: str = None) -> str:
        try:
            compound = pcp.get_compounds(compound_name, 'name')[0]
            smiles = compound.canonical_smiles
            return f"{smiles}"
        except:
            return ""

    async def _arun(self, compound_name: str = None) -> str:
        """Use the HelloTool asynchronously."""
        return self._run(compound_name)