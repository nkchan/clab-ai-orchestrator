# Labs

Containerlab topology definitions and initial configuration files.

## Available Labs

### basic-bgp
Minimal eBGP topology with FRR + FRR.

```
FRR1 (AS65001, 192.0.2.1/30) ---- P2P ---- FRR2 (AS65002, 192.0.2.2/30)
     Lo: 10.0.0.1/32                         Lo: 10.0.0.2/32
```

```bash
# Deploy
sudo clab deploy -t labs/basic-bgp/topology.clab.yml

# Inspect
sudo clab inspect -t labs/basic-bgp/topology.clab.yml

# Destroy
sudo clab destroy -t labs/basic-bgp/topology.clab.yml
```
