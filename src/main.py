import os, random
import matplotlib.pyplot as plt
from agents_utils import RandomAgent, AlwaysDoNothingAgent, AlwaysSwitchAgent, TrackLifeAgent, StatAgent
from sim_utils import Simulator


def homo_exp(n):
    full_info_losses = {"tele": [], "dele": []}
    part_info_losses = {"tele": [], "dele": []}
    loss_dicts = [part_info_losses, full_info_losses]
    agent_cons_arr = [RandomAgent, AlwaysDoNothingAgent,
                    AlwaysSwitchAgent, TrackLifeAgent, StatAgent]
    agent_label_arr = [str(Cons(0)) for Cons in agent_cons_arr]

    for full_info in [0, 1]:
        print(f"start homogenous experiments, full_info={full_info}, n={n}")
        simulator = Simulator(n=n, full_info=full_info, seed=0)

        for Cons in agent_cons_arr:
            agent_arr = [Cons(0) for i in range(n)]
            simulator.batch_set_trollies(agent_arr)
            for i in range(1000):
                simulator.refresh_track_nums()
                simulator.refresh_pass_nums()
                simulator.run_trial()

            tele_loss = simulator.get_tot_tele_loss()
            dele_loss = simulator.get_tot_dele_loss()
            print(f"{agent_arr[0]}: tele_loss={tele_loss:.3f},"
                  f"dele_loss={dele_loss:.3f}")
            loss_dicts[full_info]['tele'].append(tele_loss)
            loss_dicts[full_info]['dele'].append(dele_loss)
            simulator.clear_records()
        print()

    plot_dir = "../plots"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    plot_url = os.path.join(plot_dir, f"homo_exp_loss_plot_n={n}.png")
    title = f"homogenous experiment loss plot n={n}"
    plot_losses(plot_url, title, loss_dicts, agent_label_arr)


def mix_exp(n):
    full_info_losses = {"tele": [], "dele": []}
    part_info_losses = {"tele": [], "dele": []}
    loss_dicts = [part_info_losses, full_info_losses]

    agent_cons_arr = [RandomAgent, AlwaysDoNothingAgent,
                      AlwaysSwitchAgent, TrackLifeAgent, StatAgent]
    agent_label_arr = [str(Cons(0)) for Cons in agent_cons_arr]
    if n % len(agent_label_arr) != 0:
        raise ValueError(f"n={n} not a divisible by number of"
                         f"agent types={len(agent_label_arr)}")
    agent_arr = []
    for i in range(n//len(agent_cons_arr)):
        for Cons in agent_cons_arr:
            agent_arr.append(Cons(0))
    random.shuffle(agent_arr)
    agent_str_arr = [str(agent) for agent in agent_arr]
    assert len(agent_arr) == len(agent_str_arr) == n

    for full_info in [0, 1]:
        print(f"start mixed experiments, full_info={full_info} n={n}")
        simulator = Simulator(n=n, full_info=full_info, seed=0)
        simulator.batch_set_trollies(agent_arr)
        for i in range(1000):
            simulator.refresh_track_nums()
            simulator.refresh_pass_nums()
            simulator.run_trial()

        for label in agent_label_arr:
            indices = [i for i, x in enumerate(agent_str_arr) if x == label]
            tele_loss = simulator.get_tele_loss_by_idx(indices)
            dele_loss = simulator.get_dele_loss_by_idx(indices)
            print(f"{label}: tele_loss={tele_loss:.3f}, dele_loss={dele_loss:.3f}")
            loss_dicts[full_info]['tele'].append(tele_loss)
            loss_dicts[full_info]['dele'].append(dele_loss)
        print()

    plot_dir = "../plots"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    plot_url = os.path.join(plot_dir, f"mix_exp_loss_plot_n={n}.png")
    title = f"mixed experiment loss plot n={n}"
    plot_losses(plot_url, title, loss_dicts, agent_label_arr)


def plot_losses(plot_url, title, loss_dicts, agent_label_arr):
    
    full_loss = loss_dicts[0]
    part_loss = loss_dicts[1]

    if "tele" not in full_loss or "dele" not in full_loss or \
            "tele" not in part_loss or "dele" not in part_loss:
        raise ValueError("loss dict doesn't contain required keys:"
                         "tele\", \"dele\"")

    fig, axes = plt.subplots(1, 2, figsize=[15, 6])
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.suptitle(title, fontsize=20)

    axes[0].plot(agent_label_arr, part_loss["tele"], label="partical information", marker="o")
    axes[0].plot(agent_label_arr, full_loss["tele"], label="full information", marker="o")
    axes[0].set_title("teleology information")
    axes[0].legend()

    axes[1].plot(agent_label_arr, part_loss["dele"], label="partial information", marker="o")
    axes[1].plot(agent_label_arr, full_loss["dele"], label="full information", marker="o")
    axes[1].set_title("deleology information")
    axes[1].legend()

    print(f"save loss plot at={plot_url}")
    fig.savefig(plot_url)


def main():
    simulator = Simulator(n=5, full_info=0, seed=0)

    randAg = RandomAgent(0)
    adnAg = AlwaysDoNothingAgent(0)
    asAg = AlwaysSwitchAgent(0)
    tlAg = TrackLifeAgent(0)
    statAg = StatAgent(0)
    agent_arr = [randAg, adnAg, asAg, tlAg, statAg]
    simulator.batch_set_trollies(agent_arr)
    for i in range(20):
        simulator.refresh_track_nums()
        simulator.refresh_pass_nums()
        simulator.run_trial()
        print(simulator.get_tot_tele_loss())
        print(simulator.get_tot_dele_loss())



if __name__ == "__main__":
    # main()
    for n in [2, 5, 15, 20, 50, 100]:
        homo_exp(n)
    for n in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]:
        mix_exp(n)
