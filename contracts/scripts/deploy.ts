import { ethers } from "hardhat";

async function main() {
  const ModelRegistry = await ethers.getContractFactory("ModelRegistry");
  const registry = await ModelRegistry.deploy();
  await registry.waitForDeployment();

  const address = await registry.getAddress();
  console.log(`ModelRegistry deployed to: ${address}`);
  console.log(`Set MODEL_REGISTRY_ADDRESS=${address} in your .env file`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
