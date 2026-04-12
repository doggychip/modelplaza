import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";

const config: HardhatUserConfig = {
  solidity: "0.8.24",
  networks: {
    "base-sepolia": {
      url: process.env.CHAIN_RPC_URL || "https://sepolia.base.org",
      accounts: process.env.CHAIN_PRIVATE_KEY
        ? [process.env.CHAIN_PRIVATE_KEY]
        : [],
    },
    base: {
      url: "https://mainnet.base.org",
      accounts: process.env.CHAIN_PRIVATE_KEY
        ? [process.env.CHAIN_PRIVATE_KEY]
        : [],
    },
  },
};

export default config;
