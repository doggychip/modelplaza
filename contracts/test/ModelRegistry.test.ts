import { expect } from "chai";
import { ethers } from "hardhat";

describe("ModelRegistry", function () {
  async function deployFixture() {
    const [owner, other] = await ethers.getSigners();
    const ModelRegistry = await ethers.getContractFactory("ModelRegistry");
    const registry = await ModelRegistry.deploy();
    return { registry, owner, other };
  }

  it("should register a model", async function () {
    const { registry, owner } = await deployFixture();
    const hash = ethers.keccak256(ethers.toUtf8Bytes("model-weights-v1"));

    await expect(registry.registerModel(hash, "alice/my-model", "apache-2.0"))
      .to.emit(registry, "ModelRegistered")
      .withArgs(hash, "alice/my-model", "apache-2.0", owner.address, 1);
  });

  it("should reject duplicate registration", async function () {
    const { registry } = await deployFixture();
    const hash = ethers.keccak256(ethers.toUtf8Bytes("model-weights-v1"));

    await registry.registerModel(hash, "alice/my-model", "apache-2.0");
    await expect(
      registry.registerModel(hash, "alice/my-model", "apache-2.0")
    ).to.be.revertedWith("Already registered");
  });

  it("should verify a registered model", async function () {
    const { registry, owner } = await deployFixture();
    const hash = ethers.keccak256(ethers.toUtf8Bytes("model-weights-v1"));

    await registry.registerModel(hash, "alice/my-model", "mit");
    const [slug, license, registrant, , version] =
      await registry.verifyModel(hash);

    expect(slug).to.equal("alice/my-model");
    expect(license).to.equal("mit");
    expect(registrant).to.equal(owner.address);
    expect(version).to.equal(1);
  });

  it("should track version history", async function () {
    const { registry } = await deployFixture();
    const hash1 = ethers.keccak256(ethers.toUtf8Bytes("v1"));
    const hash2 = ethers.keccak256(ethers.toUtf8Bytes("v2"));

    await registry.registerModel(hash1, "alice/my-model", "apache-2.0");
    await registry.registerModel(hash2, "alice/my-model", "apache-2.0");

    expect(await registry.getVersionCount("alice/my-model")).to.equal(2);
    expect(await registry.getVersionHash("alice/my-model", 0)).to.equal(hash1);
    expect(await registry.getVersionHash("alice/my-model", 1)).to.equal(hash2);
  });

  it("should reject verify for unregistered model", async function () {
    const { registry } = await deployFixture();
    const hash = ethers.keccak256(ethers.toUtf8Bytes("unknown"));

    await expect(registry.verifyModel(hash)).to.be.revertedWith(
      "Not registered"
    );
  });
});
